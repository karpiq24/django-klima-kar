/*
* C++ implementation of NRV2E decompression algorithm
* which was used in this project to decode
* Aztec 2D from Polish Vehicle Registration Documents
* - by http://haker.info A.D. 2019
* slightly modifed by Bartosz Karpiński 2019
*
* Based on original UCL library written by:
* Markus F.X.J. Oberhumer <markus@oberhumer.com>
* http://www.oberhumer.com/opensource/ucl/
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*/

#include <iostream>
#include <string>
#include <vector>

const int START_OFFSET = 4;
std::vector<unsigned char> src;
int ilen = START_OFFSET;
int currentByte;
int currentBit;

static unsigned char GetBit()
{
    if (ilen >= src.size())
        throw std::invalid_argument("Przesunięcie jest poza zakresem.");

    if (currentBit == 0)
    {
        currentByte = src[ilen++];
        currentBit = 8;
    }

    return (unsigned char)(((unsigned int)currentByte >> --currentBit) & 1);
}

static std::vector<unsigned char> DecompressNRV2E(std::vector<unsigned char> sourceData)
{
    src = sourceData;

    int destSize = src[0] | (int)src[1] << 8 | (int)src[2] << 16 | (int)src[3] << 24;
    std::vector<unsigned char> dst(destSize);

    unsigned int olen = 0, last_m_off = 1;

    while (ilen < src.size())
    {
        unsigned int m_off, m_len;

        while (GetBit() == 1)
        {
            dst[olen++] = src[ilen++];
        }

        m_off = 1;
        while (true)
        {
            m_off = m_off * 2 + GetBit();
            if (GetBit() == 1) break;
            m_off = (m_off - 1) * 2 + GetBit();
        }

        if (m_off == 2)
        {
            m_off = last_m_off;
            m_len = GetBit();
        }
        else
        {
            m_off = (m_off - 3) * 256 + src[ilen++];
            if (m_off == 0xffffffff)
                break;
            m_len = (m_off ^ 0xffffffff) & 1;
            m_off >>= 1;
            last_m_off = ++m_off;
        }
        if (m_len > 0)
            m_len = (unsigned int)1 + GetBit();
        else if (GetBit() == 1)
            m_len = (unsigned int)3 + GetBit();
        else
        {
            m_len++;
            do
            {
                m_len = m_len * 2 + GetBit();
            } while (GetBit() == 0);
            m_len += 3;
        }
        m_len += (unsigned int)(m_off > 0x500 ? 1 : 0);

        unsigned int m_pos;
        m_pos = olen - m_off;

        dst[olen++] = dst[m_pos++];
        do dst[olen++] = dst[m_pos++]; while (--m_len > 0);
    }
    return dst;
}

static std::string base64_decode(const std::string &in) {

    std::string out;

    std::vector<int> T(256, -1);
    for (int i = 0; i < 64; i++)
        T["ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"[i]] = i;

    int val = 0, valb = -8;
    for (unsigned char c : in)
    {
        if (T[c] == -1) break;
        val = (val << 6) + T[c];
        valb += 6;
        if (valb >= 0)
        {
            out.push_back(char((val >> valb) & 0xFF));
            valb -= 8;
        }
    }
    return out;
}

std::wstring decodeAztec(std::string code)
{
    if (code.length() % 2 == 1)
    {
        code[code.length() - 1] = '\0';
    }

    std::string decoded = base64_decode(code);
    std::vector<unsigned char> decodedVec = std::vector<unsigned char>(decoded.begin(), decoded.end());

    std::vector<unsigned char> decompressed = DecompressNRV2E(decodedVec);

    std::wstring plainData(decompressed.begin(), decompressed.end());

    std::wcout << plainData << std::endl;
    return plainData;
}

int main(int argc, char *argv[])
{
    setlocale( LC_ALL, "C.UTF-16" );
    decodeAztec(argv[1]);

#if _DEBUG
    getchar();
#endif
    return EXIT_SUCCESS;
}
